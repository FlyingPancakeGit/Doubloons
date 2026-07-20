from settings import *


def generate_hue(background_colour, gradient_colour, canvas_size):
    surf = pygame.Surface((canvas_size[0], canvas_size[1]), pygame.SRCALPHA)
    surf.fill(background_colour)

    map = pygame.Surface((canvas_size[0], canvas_size[1]), pygame.SRCALPHA)

    pixel_array = np.zeros([canvas_size[0], canvas_size[1], 3], dtype=np.uint8)
    pixel_array[:, :] = gradient_colour
    colour_map = pygame.surfarray.make_surface(pixel_array)

    map.blit(colour_map, (0, 0))

    # create alpha values array
    alpha_map = np.zeros([canvas_size[0], canvas_size[1]], dtype=np.uint8)

    for index, value in np.ndenumerate(alpha_map):
        alpha_map[index] = 255 * ((index[1] / canvas_size[1]) ** 2)

    alpha_view = pygame.surfarray.pixels_alpha(map)
    alpha_view[:] = alpha_map
    del alpha_view

    surf.blit(map, (0, 0))

    return surf